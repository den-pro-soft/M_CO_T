

// reusable function based on official doc
// https://facebook.github.io/react/docs/forms.html
export default function handleInputChange(event) {
      const target = event.target;
      const name = target.name;
      const value = target.value;
      if (target.type !== 'checkbox') {
        this.setState({
            [name]: value
        });
      } else {
        const checked = target.checked;
        if (!value || value === 'on') {
          this.setState({
              [name]: checked
          });
        } else {
          const values = this.state[name] || [];
          if (checked) {
              values.push(value);
          } else {
              const indexOf = values.indexOf(value);
              if (indexOf >= 0) {
                values.splice(indexOf, 1);
              }
          }
          this.setState({
             [name]: values
          });
        }
      }
}
