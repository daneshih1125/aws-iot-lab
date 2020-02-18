'use strict';
const AWS = require('aws-sdk');
const db = require('./db_connect');

AWS.config.region = process.env.AWS_REGION;
const iotdata = new AWS.IotData({
  endpoint: process.env.IOT_ENDPOINT,
  accessKeyId: process.env.ACCESS_KEY_ID,
  secretAccessKey: process.env.SECRET_ACCESS_KEY
})

module.exports.eventRecv = (event, context, callback) => {
  context.callbackWaitsForEmptyEventLoop = false;
  
  var recv_time = Math.floor(Date.now() / 1000);
  const data = {
    'device_id': event.device_id,
    'created_at': new Date(event.created_at * 1000),
    'received_at': new Date(recv_time * 1000),
  };
  
  db.insert('iot_event', data)
    .then(res => {
      callback(null, {
        statusCode: 200,
        body: "Recv " + res
      })
    })
    .catch(e => {
      callback(null, {
        statusCode: e.statusCode || 500,
        body: "Failed to save event " + e
      })
    });
};

module.exports.motorCtrl = (event, context, callback) => {
  context.callbackWaitsForEmptyEventLoop = false;
  console.log(event.body);
  const jsonData = JSON.parse(event.body);
  var params = {
    payload: `{"state":{"desired":{"motor_enable":${jsonData.motor_enable}}}}`,
    thingName: process.env.THING_NAME
  }
  iotdata.updateThingShadow(params, (err, data) => {
    if (err) {
      console.log(err);
      callback(null, {
        statusCode: 500,
        body: 'Error: Could not find Todos: ' + err,
      });
    } else {
      console.log('update OK.');
      callback(null,{
        statusCode: 200,
        body: JSON.stringify({'motor_enable': jsonData.motor_enable}),
      });
    }
  })
};
