class textAreaSerialConsole {
    constructor(element, onInput) {
        this.onInput = onInput;
        this.element = element;
        this.text = "";
        this.event_func = this.#evInput.bind(this);
        addEventListener('input', this.event_func);
    }

    destroy() {
        removeEventListener('input', this.event_func);
    }

    addText(str) {
        for (let i = 0; i < str.length; i++) {
            const char = str.charAt(i);
            if (char == String.fromCharCode(8)) { // ASCII 8 -> backspace
                this.text = this.text.slice(0, this.text.length - 1);
            } else {
                this.text += char;
            }
        }
        if (this.text.length > 4000) {
            this.text = this.text.slice(Math.floor(this.text.length / 2), this.text.length);
        }
        this.#resetValue();
    }

    #moveCursorToEnd() {
        this.element.scrollTop = this.element.scrollHeight;
        this.element.selectionStart = this.element.selectionEnd = this.element.value.length;
    }

    #resetValue() {
        this.element.value = this.text;
        this.#moveCursorToEnd();
    }

    #evInput(event) {
        if ((this.element.value.length >= this.text) || (this.element.value.slice(0, this.text.length) === this.text)) {
            let inpStr = this.element.value.slice(this.text.length);
            this.onInput(inpStr);
        } else {
            // TODO: handle multiple backspaces
            // try to handle single backspace
            if (this.element.value.slice(0, this.text.length - 1) === this.text.slice(0, this.text.length - 1)) {
                this.onInput(String.fromCharCode(8)); // ASCII 8 -> backspace
            }
        }
        this.#resetValue();
    }
}
