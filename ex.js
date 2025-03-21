fetch('http://localhost:3000/api/crew/choose_name/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ criteria: 'I want a name that works for german french and english at the same time' })
})
.then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    return new ReadableStream({
        start(controller) {
            function push() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        controller.close();
                        return;
                    }
                    const chunk = decoder.decode(value);
                    chunk.split('\n').forEach(line => {
                        if (line) {
                            const data = JSON.parse(line);
                            console.log(data); // Handle logs and result
                        }
                    });
                    push();
                });
            }
            push();
        }
    });
});
