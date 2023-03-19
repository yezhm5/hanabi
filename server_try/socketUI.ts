const { io } = require('socket.io-client')

const socket = io('http://0.0.0.0:5000')

socket.on('connect', () => {
    console.log('已连接服务端')
})

socket.emit('my_message', 'hello')
/*** socket receive message ***/
socket.on('message', (data) => {
    console.log(data)
})

socket.on('disconnect', () => {
    console.log('已断开连接')
})
