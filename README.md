# pytest-stepper-plugin
A Pytest plugin created to help with making *simple* tests.

## Installation
If you need the plugin, just copy the `stepper.py` file to your project and add it to `pytest_plugins` in `conftest.py` like this:
```python
pytest_plugins = [
    "stepper",
    # other plugins...
]
```
Also, since this is a *template* repository, you can [generate a new project based on this one](https://github.com/RMuskovets/pytest-stepper-plugin/generate).


## Usage
A example module with steps for a test is located [here, in `steps.py`](https://github.com/RMuskovets/pytest-stepper-plugin/blob/master/steps.py).

Here's one another simple step:
```python
def my_simple_step():
    def my_simple_step(vars):
        print('hello, world!')
    return my_simple_step
```
Steps consist of 2 function: "configuration" function and the actual step, which is nested in it.  
I made it like this because some steps can require configuration.  
For example, if you're using Selenium, you could have a step `go_to` that accepts the URL as a parameter.

The actual step function takes only 1 argument `vars`: a `dict` where you can save variables for use in other steps.  
Continuing the Selenium example, you can have a `open_browser` step that opens the browser window and saves it in `vars` for later use.

Here's the code for these 2 steps:
```python
def open_browser():
    def open_browser(vars):
        window = Chrome()
        vars['browser'] = window
    return open_browser

def go_to(url):
    def go_to(vars):
        window = vars['browser']
        window.get(url)
    return go_to
```

## More!
Check out [this project's wiki](https://github.com/RMuskovets/pytest-stepper-plugin/wiki) to find more information.
