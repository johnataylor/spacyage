
const restify = require('restify');

state = new Set()

function respondToPut(req, res, next) {
    var item = req.params.item;
    console.log('PUT ' + item);
    if (state.has(item)) {
        res.send(200, {})
    }
    else {
        state.add(item)
        res.send(201, {});
    }
}

function respondToDelete(req, res, next) {
    var item = req.params.item;
    console.log('DELETE ' + item);
    if (state.has(item)) {
        state.delete(item);
        res.send(200, {})
    }
    else {
        res.send(404, {});
    }
}

function respondToGet(req, res, next) {
    console.log('GET');
    result = Array.from(state).join(',');
    res.send(200, result);
}

const server = restify.createServer();

server.put('/form/:item', respondToPut);
server.del('/form/:item', respondToDelete);
server.get('/form', respondToGet);

server.listen(8080, function() {
    console.log('%s listening at %s', server.name, server.url);
});
