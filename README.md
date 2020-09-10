# ADC data pipeline
There are a lot of different steps involved in data science projects. For example: fixing data quality issues, feature engineering, parameter tuning and reporting your results. Although these steps are often approximately the same, the approach is not necessarily the same. The data and the goal of the project determines the way you manipulate your data and what model you need. In turn, your model choice determines what kind of parameter tuning you need to do and how you are going to present your results. In other words, there are a lot of data-science-paths to walk. The more you program, the more you might get drowned in an ever increasing amount of if-statements, giving the feeling that you lose grip on the structure in your project. This package aims to solve that problem, by offering a more structured way of working.

## Basic principles
To structure our project, we need to follow three steps:
1. Build your own `Pipeline` class.
2. Loading your (run) configuration.
3. Running the pipeline.

Below, each step will be explained.

### 1. Build your own `Pipeline` class
Import the `adcpipeline` package and import the `PipelineBase` class:
```
from adcpipeline import PipelineBase
```
And build your own `Pipeline` class by inheriting from PipelineBase:
```
class Pipeline(PipelineBase):
    pass
```
This doesn't do anything yet, so let's add a few steps in our `Pipeline`. We do this by adding methods we want to execute when we run the Pipeline. The example below adds three methods to this specific `Pipeline`:
```
class Pipeline(PipelineBase):
    def print_text_from_argument(self, text='asfd'):
        print(text)

    def print_predefined_text(self):
        print('Predefined text')

    def n_times_squared(self, value: int, n: int):
        result = value
        for i in range(0, n):
            result = result ** 2
        print(f'Squaring the number {value} for {n} times in a row gives = {result}')
```

### 2. Loading your (run) configuration.
When we want to intantiate the `Pipeline`, we need to pass de data as an argument (`df`) and we need to pass our run configuration as an argument (`method_settings`):
```
p = Pipeline(df=data, method_settings=method_settings)
```
The variable `data` can be any data, as long as it is a Pandas DataFrame. The `method_settings` variable is a list containing dictionaries, which define (in order) how all the methods are going to be executed once our `Pipeline` runs. Each dictionary contains the method (name) that needs to be called. The values are a dictionary of arguments (names) with their corresponding argument value that is going to be passed to the method. An example will make things clear:
```
method_settings = [
    {'print_text_from_argument': {'text': 'This is the text passed to the method'}},
    {'print_text_from_argument': {'text': 1}},
    {'print_predefined_text': None},
    {'n_times_squared': {'value': 2, 'n': 2}},
    {'print_text_from_argument': {'text': 'Same method is called again, but later in the pipeline'}}
]
```
Here we see that the method `print_text_from_argument` is called two times with a `text` argument. This `text` argument is different each time. After that the other two methods are called and lastly, `print_text_from_argument` is called one last time.

The `method_settings` as defined in the example above takes up a lot of lines and every time we make an additional `method_settings`, we get more lines of code. It is therefore recommended to load the `method_settings` from a configuration file instead. You can define your pipeline settings in a .yaml file and let the pipeline class load this file:
```
p = Pipeline.from_yaml_file(df=data, path=f'{root_dir}/configs/<YOUR_METHOD_SETTINGS>.yaml')
```
The .yaml file would then look like this:
```
pipeline:
  - print_text_from_argument: {text: 'This is the text passed to the method'}
  - print_text_from_argument: {text: 1}
  - print_predefined_text:
  - n_times_squared: {value: 2, n: 2}
  - print_text_from_argument: {text: 'Same method is called again, but later in the pipeline'}
```

