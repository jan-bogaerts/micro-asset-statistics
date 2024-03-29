# micro-asset-statistics
A micro service that provides real-time statistics for assets. It contains an api interface to specify which statistics need to be calculated on which assets, using which type of grouping

# example
an example of the json structure that should be sent to the microservice:

```json

{
  "name": "jan's first test",
  "username": "testjan",
  "pwd": "testtestjan",
  "asset":"5UJ5solx5AKeBYG4JUJruyH0",
  "comment": "this is a def for 1 asset. Each group should be for a unique timeslot",
  "groups":[
    {
      "comment": "reset is expressed as every 'year:month:week:day:hour:minute', so in this case it's every day. The name field is used to help identify assets related to this group",
      "reset": "0:0:0:1:0:0",
      "name": "every_day",
      "calculate":[
        {"function": "count"},
        {"function": "min"},
        {"function": "max"},
        {"function": "avg"},
        {"function": "std"},
        {"function": "distribution", "bucketsize": 2}
      ]
    },
    {
      "name": "always",
      "comment": "when no reset, values are never reset",
      "calculate":[
        {"function": "count"},
        {"function": "distribution", "bucketsize": 2}
      ]
    }
  ]

}

```
