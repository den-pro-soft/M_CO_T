# MinTax

This project contains both the HTML5 web client (webapp folder) and the backend API (api folder) for MinTax.

## Development

### Database

* `cd db`

#### Prerequisites

You'll need Python 3.6+ installed on your computer. You'll also need a PostgreSQL server accepting connections
on `localhost:5432`, with a user/password `postgres/postgres` and an empty `mintax` database. Finally you'll need
a Redis server accepting connections on `localhost:6379`.

#### Setup

Create a virtual environment (optional but highly recommended):

```
python -m venv venv
```

You only need to do that once. You will need to activate it for every new terminal, however:

```
source venv/bin/activate
```

Install/update dependencies:

```
pip install -r requirements.txt
```

#### Run Migrations/Upgrade the Database

```
alembic upgrade head
```

#### Maintenance Script

It is advisable to run the below script periodically on any long-lived environment:

```
delete from traveller_data -- this will cascade to travels
where id in (select td.id
             from traveller_data td
               left join traveller_data_periods tdp
                 on tdp.traveller_data_id = td.id
             where td.upload_date + interval '1 day' < now() -- older than 24 hours
             and tdp is null) -- not related to any period

delete from report_results
where id in (select rr.id
             from report_results rr
             where rr.version_ts < (select cust.last_available_travel_history
                                    from customers cust
                                    where cust.id = rr.customer_id))

delete from employee_travel_history
where id in (select ee.id
             from employee_travel_history ee
             where ee.version_ts < (select cust.last_available_travel_history
                                    from customers cust
                                    where cust.id = ee.customer_id))

vacuum verbose
--or vacuum full verbose, if this is a development box to free disk space to the OS
```

Use this to check disk usage on a table per table basis (and run VACUUM apropriatelly to free server resources):

```
SELECT *, pg_size_pretty(total_bytes) AS total
    , pg_size_pretty(index_bytes) AS INDEX
    , pg_size_pretty(toast_bytes) AS toast
    , pg_size_pretty(table_bytes) AS TABLE
  FROM (
  SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
      SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME
              , c.reltuples AS row_estimate
              , pg_total_relation_size(c.oid) AS total_bytes
              , pg_indexes_size(c.oid) AS index_bytes
              , pg_total_relation_size(reltoastrelid) AS toast_bytes
          FROM pg_class c
          LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
          WHERE relkind = 'r'
  ) a
) a
ORDER BY total_bytes DESC;
```

### Backend API

* `cd api`

#### Prerequisites

You'll need Python 3.6+ installed on your computer.

#### Setup

Create a virtual environment (optional but highly recommended):

```
python -m venv venv
```

You only need to do that once. You will need to activate it for every new terminal, however:

```
source venv/bin/activate
```

Install/update dependencies:

```
pip install -r requirements.txt
```

#### Local Server

Before launching a local server, create a copy of the `env.example` file
(naming it `env`) and fill the variables accordingly.

Also be sure that you have your AWS credentials
properly configured on your machine (~/.aws/credentials).

```
export FLASK_APP=mintax.py
source ./env
flask run
```

You may also use gunicorn for development:

```
pip install gunicorn
source ./env
gunicorn -b 127.0.0.1:5000 -w 3 -k gevent mintax:app
```

#### Local Celery Worker

In order to process asynchronous work you'll need a celery worker:

```
cd api
source venv/bin/activate
source ./env
python -m celery_app worker --loglevel=info --max-tasks-per-child=1
```

#### Debugging on VSCODE

Adapt this `launch.json` to debug the application inside VSCODE:

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "API",
            "type": "python",
            "request": "launch",
            "stopOnEntry": false,
            "pythonPath": "${config.python.pythonPath}",
            "program": "${workspaceRoot}/api/venv/bin/flask",
            "env": {
                "FLASK_APP": "${workspaceRoot}/api/mintax.py",
                "MINTAX_UPLOAD_BUCKET": "etax-mintax-file-upload"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "debugOptions": [
                "WaitOnAbnormalExit",
                "WaitOnNormalExit",
                "RedirectOutput"
            ]
        }
    ]
}
```

#### Checking Code Quality

Run the following command on the repository root while inside the API virtual python environment:

```
find . -iname "*.py" -not -path "./*/venv/*" -not -path "./webapp/*" -not -path "./.vscode/*" |xargs pylint
```

#### Running Unit Tests

Run the following command on the repository root while inside the API virtual python environment:

```
pytest
```

If you want to watch automatically for changes:

```
pip install pytest-watch
ptw
```

#### AWS configuration

Follow the steps below in order to configure a new environment on AWS:

1. Launch a new EC2 instance using Amazon Linux. Remember to attach an IAM Role with S3 upload/download and SQS access so boto3 integration can work.
2. Assign an Elastic IP address to the new server.
3. Point the chosen API FQDN to the Elastic IP by adding a new A record using the domain DNS provider.
4. Generate a SSL certificate for the API FQDN. You can use a free service like http://sslforfree.com for that.
5. Connect to the new instance via SSH. Remember to use the `ec2-user`, for example: `ssh ec2-user@mintax-api.quasarconsultoria.com`.
6. Generate a key pair for the new server: `ssh-keygen`. Don't use a passphrase.
7. Add this key as a new deploy key on GitLab.
8. Install git: `sudo yum install git`.
9. Clone the repository: `git clone git@gitlab.com:samuel-grigolato/etax-mintax.git`.
10. Install python 3: `sudo yum install python36 python36-pip`.
11. Install postgresql: `sudo yum install postgresql96 postgresql96-server`.

Note that it is probably best to use a dedicated RDS instance on production environments. If you use RDS then you need to install at least
the `postgresql96` and `postgresql96-devel` packages (which contains the client binaries).

12. Init the database: `sudo service postgresql95 initdb`.
13. Change `pg_hba.conf` and `postgres.conf` (they are both located at `/var/lib/pgsql95/data/`) in order to allow Internet connections (only if this is desired).
14. Install python OS dependencies: `sudo yum install libcurl-devel python36-devel` and `sudo yum groupinstall "Development Tools"`.
14. Install virtualenv: `sudo python3 -m pip install virtualenv`.
15. Create a virtual environment for alembic:

```
cd ~/etax-mintax/db
virtualenv venv
source venv/bin/activate
```

16. Install dependencies: `pip install -r requirements.txt`.
17. Run alembic: `MINTAX_DB_URL=postgresql://mintax:mintax@localhost/mintax alembic upgrade head`
18. Create a virtual environment for the API:

```
deactivate
cd ~/etax-mintax/api
virtualenv venv
source venv/bin/activate
```

19. Install application dependencies: `PYCURL_SSL_LIBRARY=nss pip install -r requirements.txt`.
20. Install gunicorn: `pip install gunicorn`.
21. Create an upstart job for gunicorn: `sudo vim /etc/init/mintax.conf`. Paste the following contents:

```
start on (runlevel [345] and started network)
stop on (runlevel [!345] and stopping network)

respawn
chdir /home/ec2-user/etax-mintax/api

env MINTAX_DB_URL=postgresql://mintax:mintax@localhost/mintax
env MINTAX_PASSWORD_SALT=pg9FVxim21
env MINTAX_RECAPTCHA_SECRET=6LcOyCkUAAAAAJVSlIk7Kbp7a7f6Qc1K-uKY11Fg
env MINTAX_UPLOAD_BUCKET=etax-mintax-file-upload
env MINTAX_EMAIL_MAILGUN_URL=https://api.mailgun.net/v3/XXXXXXXXXXXXXXXXXXXXXXX/messages
env MINTAX_EMAIL_MAILGUN_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXX
env MINTAX_EMAIL_FROM_ADDRESS=XXXXXXXXXXXXXXXXXXXXXXXX
env MINTAX_QUEUE_NAME_PREFIX=mintax-stg-

exec /home/ec2-user/etax-mintax/api/venv/bin/gunicorn -w 3 -k gevent --timeout 900 -b unix:/tmp/gunicorn.sock --error-logfile /var/log/mintax.log mintax:app
```

Note that it is highly advisable to generate a new SALT (any string with the same length will do) for production environments.
Also, you have to adjust MINTAX_RECAPTCHA_SECRET and the EMAIL related variables to the corresponding value for the target environment.

22. Install nginx: `sudo yum install nginx`.
23. Create an upstart job for nginx: `sudo vim /etc/init/nginx.conf`. Paste the following contents:

```
start on (runlevel [345] and started network)
stop on (runlevel [!345] and stopping network)

env DAEMON=/usr/sbin/nginx
env PID=/var/run/nginx.pid

expect fork
respawn
respawn limit 10 5

pre-start script
        $DAEMON -t
        if [ $? -ne 0 ]
                then exit $?
        fi
end script

exec $DAEMON
```

24. Edit nginx configuration: `sudo vim /etc/nginx/nginx.conf`. Remove everything below the loading of modular configuration files (including it):

```
    ## REMOVE EVERYTHING BELOW THIS LINE EXCEPT THE CLOSING BRACKETS.

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;
```

25. Then add an upstream configuration pointing to the gunicorn UNIX socket:

```

    gzip on;
    gzip_disable "msie6";

    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_min_length 256;

    client_max_body_size 100M;

    upstream app_server {
            server unix:/tmp/gunicorn.sock fail_timeout=0;
    }

    server {
        listen       443 ssl http2 default_server;
        listen       [::]:443 ssl http2 default_server;
        server_name  mintax-api.quasarconsultoria.com;

        ssl_certificate "/etc/pki/nginx/server.crt";
        ssl_certificate_key "/etc/pki/nginx/server.key";
        # It is *strongly* recommended to generate unique DH parameters
        # Generate them with: openssl dhparam -out /etc/pki/nginx/dhparams.pem 2048
        ssl_dhparam "/etc/pki/nginx/dhparams.pem";
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout  10m;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers HIGH:SEED:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!RSAPSK:!aDH:!aECDH:!EDH-DSS-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA:!SRP;
        ssl_prefer_server_ciphers on;

        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_read_timeout 3600;
            proxy_pass http://app_server;
        }
    }

```

26. Create the directory for the certificate files: `sudo mkdir /etc/pki/nginx`.
27. Generate unique DH parameters: `sudo openssl dhparam -out /etc/pki/nginx/dhparams.pem 2048`.
28. Upload the certificate and private key to the server. Put them on the `/etc/pki/nginx` following the names on the configuration.
29. Create an upstart job for Celery: `sudo vim /etc/init/mintax-celery.conf`. Paste the following contents:

```
start on (runlevel [345] and started network)
stop on (runlevel [!345] and stopping network)

respawn
chdir /home/ec2-user/etax-mintax/api

env MINTAX_DB_URL=postgresql://mintax:mintax@localhost/mintax
env MINTAX_PASSWORD_SALT=pg9FVxim21
env MINTAX_RECAPTCHA_SECRET=6LcOyCkUAAAAAJVSlIk7Kbp7a7f6Qc1K-uKY11Fg
env MINTAX_UPLOAD_BUCKET=etax-mintax-file-upload
env MINTAX_EMAIL_MAILGUN_URL=https://api.mailgun.net/v3/XXXXXXXXXXXXXXXXXXXXXXX/messages
env MINTAX_EMAIL_MAILGUN_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXX
env MINTAX_EMAIL_FROM_ADDRESS=XXXXXXXXXXXXXXXXXXXXXXXX
env MINTAX_QUEUE_NAME_PREFIX=mintax-stg-

exec /home/ec2-user/etax-mintax/api/venv/bin/python -m celery_app worker -P solo --loglevel=WARNING --max-tasks-per-child=1 --logfile=/var/log/mintax-celery.log
```

Make sure you use the same values as for `mintax.conf`.

Note: `-P solo` is used above to solve a 100% CPU usage spike hat occurs sometimes with the default prefork pool class.
More details can be seen here: https://github.com/celery/celery/issues/3712.

30. Install redis (be sure to fetch the latest version available):

```
# Source: https://medium.com/@andrewcbass/install-redis-v3-2-on-aws-ec2-instance-93259d40a3ce

cd /usr/local/src
sudo wget http://download.redis.io/releases/redis-4.0.1.tar.gz

sudo tar xzf redis-4.0.1.tar.gz
sudo rm -f redis-4.0.1.tar.gz

cd redis-4.0.1
sudo make distclean
sudo make

sudo yum install -y tcl
sudo make test

sudo mkdir -p /etc/redis /var/lib/redis /var/redis/6379
sudo cp src/redis-server src/redis-cli /usr/local/bin
sudo cp redis.conf /etc/redis/6379.conf

sudo vim /etc/redis/6379.conf
# make these changes:
# daemonize yes                                 //at line 136
# logfile "/var/log/redis_6379.log"             //at line 171
# dir /var/redis/6379                           //at line 263
# if you are deploying a distributed environment make sure to also
# change the `bind` directive from 127.0.0.1 to something other i.e.
# 0.0.0.0 and `protected-mode` to no. Of course you need to ensure
# that redis is *not* accessible from outside the internal network
# its container resides.

sudo wget https://raw.githubusercontent.com/saxenap/install-redis-amazon-linux-centos/master/redis-server
sudo mv redis-server /etc/init.d
sudo chmod 755 /etc/init.d/redis-server

sudo vim /etc/init.d/redis-server
# REDIS_CONF_FILE="/etc/redis/6379.conf"                 //line 26

sudo chkconfig --add redis-server
sudo chkconfig --level 345 redis-server on
sudo service redis-server start

sudo vim /etc/sysctl.conf
## ensure redis background save issue
# vm.overcommit_memory = 1

sudo sysctl vm.overcommit_memory=1

# test installation
redis-cli ping
```

31. Start the services:

```
sudo initctl start mintax
sudo initctl start nginx
sudo initctl start mintax-celery
```

32. Add some credentials to the `users` table in order to be able to login. Get a Base64 SHA-256 hash
of `SALT + password` to put on the `password` column. Be aware that some online Base64 hash generators
DON'T put a trailing padding sign `=`, so you may need to put it yourself.

#### Deploy to an Existing AWS Environment

In order to update an existing AWS environment run the following inside the EC2 instance:

```
cd ~/etax-mintax
git pull
cd db
source venv/bin/activate
MINTAX_DB_URL=postgresql://mintax:mintax@localhost/mintax alembic upgrade head
deactivate
cd ../api
source venv/bin/activate
PYCURL_SSL_LIBRARY=nss pip install -r requirements.txt
sudo initctl stop mintax
sudo initctl start mintax
sudo initctl stop mintax-celery
sudo initctl start mintax-celery
```

### HTML5 Web Client

* `cd webapp`

#### Prerequisites

You'll need the following software installed on your computer:

* [Node.js](https://nodejs.org/) (with NPM)
* AWS CLI

#### Setup

Run the dependency manager:

* `npm install`

#### Local Server

* `npm start`

Then point your browser to `http://localhost:8080`.

#### Deploy

```
rm -rf dist
MINTAX_API_BASE_URL=https://mintax-api.quasarconsultoria.com/ MINTAX_RECAPTCHA_SITEKEY=6LcOyCkUAAAAAJ5MjzhRbWdYC7b4AqDVyDvJ0BMf npm run build
cd dist
```

Note that you have to adjust MINTAX_API_BASE_URL and MINTAX_RECAPTCHA_SITEKEY for the specifics of the target environment.

AWS S3 hosting:

```
aws s3 sync --delete . s3://etax-mintax
aws cloudfront create-invalidation --distribution-id E3QZPXACSTYPZT --paths /index.html /bundle.js
```

Google Cloud Storage (deprecated):

```
gsutil rsync -R -d . gs://mintax-webapp
gsutil acl ch -u AllUsers:R gs://mintax-webapp/*
gsutil setmeta -h "Content-Type:text/html" \
  -h "Cache-Control:private, max-age=0, no-transform" gs://mintax-webapp/index.html
```

#### Configuring a new AWS S3 bucket

In order do create a bucket for hosting this webapp follow the steps below:

1. Create a new bucket with standard options
2. Access the newly created bucket properties and enable `Static website hosting`.
3. Fill in `Index document` with index.html.
4. Go to the `Permissions` tab.
5. Under `Bucket policyc` past the content below:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::mintax-frontend/*"
        }
    ]
}
```

Important note: remember to update the `Resource` property so it reflects the correct bucket name.

6. Go to the `CloudFront` service page.
7. Click on `Create Distribution`.
8. Select `Web`.
9. Select the correct S3 bucket under `Origin domain name`.
10. Select `Use Only US, Europe and Canada` under `Price Class`.
11. Select the appropriate custom SSL certificate for SSL support. If it isn't imported yet open
a tab and access the `ACM` (AWS Certificate Manager) service. Please note that CloudFront only recognizes
certificates imported in the `N. Virginia` (us-east-1) region.
12. Fill in `Alternate Domain Names (CNAMEs)` with the appropriate FQDN.
13. Fill in `Default Root Object` with `index.html`.
14. Select `Redirect HTTP to HTTPS` in `Viewer Protocol Policy`.
15. Click on `Create Distribution`.
16. Navigate to the tab `Error Pages`. Add a record for the 403 status code, customizing the response to `/`
and a 200 response code.
17. The last but not least step is to add a CNAME (if subdomain) or a total redirect to the cloudfront
public DNS on your domain management tool.
