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
This doesn't do anything yet, so let's add a few steps in our `Pipeline`:
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
We now have added three different methods we want to execute when we run the Pipeline.
