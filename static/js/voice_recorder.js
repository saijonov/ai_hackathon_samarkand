/*
 * Voice recorder used by the patient and protocol forms.
 * Records audio, sends it to /transcribe-audio/ and shows the transcript.
 *
 *   VoiceRecorder(rootElement, { onTranscript: function (text) {} })
 *
 * The root element switches its data-state between idle, rec and busy.
 */
(function () {
    function toast(message) {
        if (window.aidToast) { window.aidToast(message); } else { window.alert(message); }
    }

    function fmt(seconds) {
        var m = Math.floor(seconds / 60);
        var s = seconds % 60;
        return m + ':' + (s < 10 ? '0' : '') + s;
    }

    window.VoiceRecorder = function (root, options) {
        options = options || {};
        var button = root.querySelector('[data-rec-btn]');
        var timeEl = root.querySelector('[data-rec-time]');
        var transcript = root.querySelector('[data-rec-transcript]');
        var recorder = null;
        var chunks = [];
        var startedAt = 0;
        var timer = null;

        function setState(state) { root.setAttribute('data-state', state); }

        if (!button) return;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            button.disabled = true;
            button.title = "Brauzer ovoz yozishni qo'llab-quvvatlamaydi";
        }

        async function start() {
            try {
                var stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                recorder = new MediaRecorder(stream);
                chunks = [];
                recorder.ondataavailable = function (e) { if (e.data.size) chunks.push(e.data); };
                recorder.onstop = function () {
                    stream.getTracks().forEach(function (t) { t.stop(); });
                    send(new Blob(chunks, { type: 'audio/webm' }));
                };
                recorder.start();
                startedAt = Date.now();
                timeEl && (timeEl.textContent = '0:00');
                timer = setInterval(function () {
                    var elapsed = Math.floor((Date.now() - startedAt) / 1000);
                    timeEl && (timeEl.textContent = fmt(elapsed));
                    if (elapsed >= 300) stop();
                }, 500);
                button.classList.add('is-rec');
                button.setAttribute('aria-label', "Yozishni to'xtatish");
                setState('rec');
            } catch (err) {
                toast("Mikrofonga ruxsat berilmadi. Brauzer sozlamalarini tekshiring.");
                setState('idle');
            }
        }

        function stop() {
            if (recorder && recorder.state !== 'inactive') recorder.stop();
            clearInterval(timer);
            button.classList.remove('is-rec');
            button.setAttribute('aria-label', 'Yozishni boshlash');
            setState('busy');
        }

        async function send(blob) {
            var form = new FormData();
            form.append('audio', blob, 'recording.webm');
            try {
                var response = await fetch('/transcribe-audio/', { method: 'POST', body: form });
                var result = await response.json();
                if (result.success) {
                    if (transcript) {
                        transcript.value = result.transcription;
                        transcript.dispatchEvent(new Event('input'));
                    }
                    if (options.onTranscript) options.onTranscript(result.transcription);
                    toast("Ovoz matnga aylantirildi. Endi AI bilan to'ldiring.");
                } else {
                    toast(result.message || 'Transkripsiyada xato');
                }
            } catch (err) {
                toast('Transkripsiya xatosi: ' + err.message);
            } finally {
                setState('idle');
            }
        }

        button.addEventListener('click', function () {
            if (root.getAttribute('data-state') === 'rec') { stop(); } else if (root.getAttribute('data-state') !== 'busy') { start(); }
        });
        setState('idle');
    };

    /* Highlight a field that was filled by AI */
    window.aidMarkFilled = function (el) {
        if (!el) return;
        var target = el.type === 'radio' || el.type === 'checkbox'
            ? (el.closest('.check-tile') || (el.id && document.querySelector('label[for="' + el.id + '"]')))
            : el;
        if (!target) return;
        target.classList.remove('ai-filled');
        void target.offsetWidth;
        target.classList.add('ai-filled');
    };
})();
