class InteractiveText extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        try {
            const data = JSON.parse(this.getAttribute('data'));
            this.render(data);
            console.log('InteractiveText connected with data:', data);
        } catch (error) {
            console.error('Failed to parse data attribute:', error);
        }
    }

    render(data) {
        const style = `
            <style>
                .fragment {
                    cursor: pointer;
                }
                .marked {
                    background-color: yellow;
                }
                .highlighted {
                    background-color: orange;
                }
            </style>
        `;

        const content = data.paragraphs.map(paragraph => {
            return `<p>${paragraph.fragments.map(fragment => {
                const className = fragment.state === 'marked' ? 'fragment marked' : 'fragment';
                return `<span class="${className}" data-id="${fragment.id}">${fragment.text}</span>`;
            }).join('')}</p>`;
        }).join('');

        this.shadowRoot.innerHTML = `${style}${content}`;
        this.addEventListeners();
    }

    addEventListeners() {
        this.shadowRoot.querySelectorAll('.fragment').forEach(fragment => {
            fragment.addEventListener('click', (event) => {
                const target = event.target;
                if (target.classList.contains('marked')) {
                    // Remove 'highlighted' class from all other fragments
                    this.shadowRoot.querySelectorAll('.highlighted').forEach(highlightedFragment => {
                        highlightedFragment.classList.remove('highlighted');
                    });

                    // Toggle 'highlighted' class on the clicked fragment
                    target.classList.toggle('highlighted');

                    const eventDetail = target.getAttribute('data-id');
                    const customEvent = new CustomEvent('interactivetext', { detail: eventDetail });
                    document.dispatchEvent(customEvent);
                    console.log(`Event 'interactivetext' transmitted with ID: ${eventDetail}`);
                }
            });
        });
    }
}

customElements.define('interactive-text', InteractiveText);