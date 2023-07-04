var hookInvokeTask;
var hookInvokeServerUrl = "{{hook_invoke_server_url}}";

// 推回处理后的数据
function hookAgentPush(url, method, id, data) {
    let sendData = { id: id, resultData: data };
    let sendJson = JSON.stringify(sendData);
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Conten-Type', 'application/json');
    xhr.onload = () => { };
    console.log(sendJson);
    xhr.send(sendJson);
}

// 拉取待处理的数据
function hookAgentGet(url, method, callBack) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);

    xhr.onreadystatechange = () => {
        if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
            let responseText = xhr.responseText;
            let responseObj = JSON.parse(responseText);
            if ("id" in responseObj && "rawData" in responseObj) {
                console.log(responseObj);
                callBack(responseObj);
            }
        }
    };
    xhr.send();
}

// 轮询任务
function loopTask(targetFuncs) {
    let resultDate;
    hookAgentGet(
        hookInvokeServerUrl,
        "GET",
        (responseObj) => {
            let id = responseObj["id"];
            let resultData = responseObj["rawData"];
            for (const func of targetFuncs) {
                resultData = func(resultData);
            }
            console.log(resultData);
            hookAgentPush(hookInvokeServerUrl, "POST", id, resultData);
        }
    );
}

// 开始Agent轮询
function startHookInvoke(targetFuncs) {
    // setInterval 理论上最小时间差是 10 毫秒，但是因为实际情况是队列中的任务并不会及时执行，耗时可能会比设置的延时时间久
    hookInvokeTask = setInterval(loopTask, 300, targetFuncs);
}

// 停止Agent轮询
function stopHookInvoke() {
    clearInterval(hookInvokeTask);
}
