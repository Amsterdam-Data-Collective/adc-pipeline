# ADC Pipeline
There are a lot of different steps involved in data science projects. For example: fixing data quality issues, feature engineering, parameter tuning and reporting your results. Although these steps are often approximately the same, the exact approach per step isn't. The data and the goal of the project determine the way you manipulate your data and what model you need. In turn, your model choice determines what kind of parameter tuning you need to do and how you are going to present your results. In other words, there are a lot of data-science-paths to walk. The more you program, the more you might get drowned in an ever increasing amount of if-statements, giving the feeling that you lose grip on the structure in your project. This package aims to solve that problem, by offering a more structured way of working.

## Installation
You can install with pip:
```
pip install adcpipeline
```

## Basic principles
To structure your project, you need to follow three steps:
1. Build your own `Pipeline` class.
2. Loading your (run) configuration.
3. Running the pipeline.

Below, each step will be explained.

### 1. Build your own `Pipeline` class
From the `adcpipeline` package import the `PipelineBase` class:
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
When we want to instantiate the `Pipeline`, we need to pass the data as an argument (`df`) and we need to pass our run configuration as an argument (`method_settings`):
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

The `method_settings` as defined in the example above takes up a lot of lines and every time we make an additional `method_settings`, we get more lines of code. It is therefore recommended to load the `method_settings` from a configuration file instead. You can define your pipeline settings in a `.yaml` file and let the pipeline class load this file:
```
p = Pipeline.from_yaml_file(df=data, path=f'{root_dir}/configs/<YOUR_METHOD_SETTINGS>.yaml')
```
The `.yaml` file would then look like this:
```
pipeline:
  - print_text_from_argument: {text: 'This is the text passed to the method'}
  - print_text_from_argument: {text: 1}
  - print_predefined_text:
  - n_times_squared: {value: 2, n: 2}
  - print_text_from_argument: {text: 'Same method is called again, but later in the pipeline'}
```

### 3. Running the pipeline.
With `method_settings` defined in step 2, we can now run our `Pipeline`:
```
p.run()
```
And that's it! By making multiple `method_settings` we can define several ways to run our `Pipeline`, without altering any of our code or writing any if statement. For example, during exploratory data analysis, it might be nice to try different things without constantly changing our code. We could then do something along the following lines:
```
p1 = Pipeline.from_yaml_file(df=data, path=f'{root_dir}/configs/<YOUR_METHOD_SETTINGS_1>.yaml')
p2 = Pipeline.from_yaml_file(df=data, path=f'{root_dir}/configs/<YOUR_METHOD_SETTINGS_2>.yaml')
p3 = Pipeline.from_yaml_file(df=data, path=f'{root_dir}/configs/<YOUR_METHOD_SETTINGS_3>.yaml')

p1.run()
p2.run()
p3.run()
```
Where each `YOUR_METHOD_SETTINGS_<N>.yaml` defines the `method_settings` per `Pipeline`. 
Alternatively the pipeline ships with a `run_or_load()` method, which can save and load the result of a pipeline from 
a .pkl file. This can be useful if you did not change the content of the pipeline, but need to rerun your script.
```
method_settings = [
    {'print_text_from_argument': {'text': 'This is the text passed to the method'}},
    {'print_text_from_argument': {'text': 1}},
    {'print_predefined_text': None},
    {'n_times_squared': {'value': 2, 'n': 2}},
    {'print_text_from_argument': {'text': 'Same method is called again, but later in the pipeline'}}
]
p = Pipeline(df=data, method_settings=method_settings, filename='my_pipeline')
p.run()  # Executes the pipeline, saves the results in cache/my_pipeline.pkl
# Some other code
p.run_or_load()  # Does not execute the pipeline but loads the content of cache/my_pipeline.pkl
# Loads the result of the first function from a pkl file and executes the remaining 4 functions
p.run_or_load(from_step=1)
``` 

## Advanced usage
- The `method_settings` dictionary is converted to actual methods with their corresponding arguments. These are saved as lambda's in the property `method_list`, which are called in order by the `run` method. You can call the methods from this list directly if you want.
- The `PipelineBase` class contains several magic methods, so that it can be used as a list. For instance, `p[0]` will return the first item in the `method_settings` property. For more info, see the magic methods in the `PipelineBase` class.
- If you have (mostly) the same data manipulations for each `Pipeline`, you can probably use just a single class as described above. However, if this class becomes extremly large and large portions of the code are evident to be only applicable to certain types of pipelines, you might consider multiple inheritance. For example, you might have completely different methods in your `Pipeline` for classification models and regression models. So you might build a `Pipeline` class as above, but make two extra classes - `PipelineClassification` and `PipelineRegression` - that inherit from your `Pipeline` class. Another example is that you maybe have timeseries and non-timeseries data. Here, too, you might consider using multiple inheritance if that seems logical.

## Other code
There is some other code in this repository used directly by `PipelineBase` or that might be useful to you. To name a few: there is a DatabaseConnection class which is a small wrapper around sqlalchemy and there is a method to load loggers. This is not explicitly explained in the README, but can be used.
