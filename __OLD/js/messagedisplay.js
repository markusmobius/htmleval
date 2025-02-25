class MessageDisplay extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
        this.updateContentMap();
        document.addEventListener('interactivetext', this.handleEvent.bind(this));
        console.log('MessageDisplay connected');
        console.log('Initial content-map:', this.getAttribute('content-map'));
    }

    disconnectedCallback() {
        document.removeEventListener('interactivetext', this.handleEvent.bind(this));
        console.log('MessageDisplay disconnected');
    }

    static get observedAttributes() {
        console.log('Observed attributes:', ['content-map']);
        return ['content-map'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === 'content-map') {
            this.updateContentMap();
            console.log('Content map attribute changed:', newValue);
        }
    }

    updateContentMap() {
        try {
            this.contentMap = JSON.parse(this.getAttribute('content-map')) || {};
            console.log('Content map updated:', this.contentMap);
        } catch (error) {
            console.error('Failed to parse content-map attribute:', error);
            this.contentMap = {};
        }
    }

    handleEvent(event) {
        const id = event.detail;
        console.log('Received interactivetext event with ID:', id);
        const content = this.contentMap[id] || [{ type: 'text', header: { text: "No text", size: 2 }, text: 'No content for this highlight' }];
        console.log('Content for ID:', content);
        this.renderContent(content);
    }

    renderContent(content) {
        const container = this.shadowRoot.querySelector('#content');
        container.innerHTML = ''; // Clear previous content

        const elements = buildContent(content, {});
        console.log('Elements:', elements);
        elements.forEach(element => container.appendChild(element));

        console.log('Updated content:', content);
    }

    render() {
        const style = `
            <style>
                #content {
                    font-size: 16px;
                    color: blue;
                }
            </style>
        `;

        const content = `
            <div id="content">Click a highlight to see the content</div>
        `;

        this.shadowRoot.innerHTML = `${style}${content}`;
    }
}

customElements.define('message-display', MessageDisplay);