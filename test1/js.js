var socket = new WebSocket("wss://ws.blockchain.info/inv");


function create_new_line_in_tabel(data) {
    data = (JSON.parse(data));
    console.log(data);
    // <td>${data.x.inputs.prev_out.addr}</td>



    for (el in data.x.out) {
        console.log(el);
        n = `
        <tr>
            <td>${data.x.out[el].addr}</td>
            <td>${data.x.out[el].value}</td>
        </tr>
        `
        document.getElementById('tables').innerHTML += n
    }


};





socket.onopen = function() {
    alert("Соединение установлено.");
};

socket.onclose = function(event) {
    if (event.wasClean) {
        console.log('Соединение закрыто чисто');
    } else {
        console.log('Обрыв соединения'); // например, "убит" процесс сервера
    }
    console.log('Код: ' + event.code + ' причина: ' + event.reason);
};

socket.onmessage = function(event) {
    // alert("Получены данные " + event.data);
    // console.log(event.data);
    create_new_line_in_tabel(event.data)
};

socket.onerror = function(error) {
    console.log("Ошибка " + error.message);
};


function test_ping() {
    let a = JSON.stringify({ "op": "ping" })
    socket.send(a)
}

function sub() {
    let a = JSON.stringify({
        "op": "unconfirmed_sub"
    })
    socket.send(a)
}

function unsub() {
    let a = JSON.stringify({
        "op": "unconfirmed_unsub"
    })
    socket.send(a)
}

function clears() {
    document.getElementById('tables').innerHTML = `
    <caption>BlockChain</caption>
    <tr>
        <th>addr</th>
        <th>value</th>

    </tr>
    <tr></tr>
    `
}