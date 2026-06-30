// Generic host block for custom web components.
//
// Mounts author-provided HTML into the eval. The HTML may include custom elements
// (Web Components) such as <lego-tree>. htmleval has NO knowledge of those
// elements — their JavaScript is inlined via addCustomElement(), and the element
// handles its own rendering and signalling through the window.htmleval signal API.
class CustomComponent {
    constructor(root, block, parent, blockID) {
        this.blockID = blockID;
        this.parent = parent;
        // Non-interactive container: completion is driven by linked question blocks.
        this.completed = [0, 0];

        var container = document.createElement("div");
        container.className = "text-content";
        root.appendChild(container);

        // Optional title.
        if (block["content"]["title"] != undefined) {
            var h = document.createElement("h" + block["content"]["title"]["size"]);
            h.innerHTML = block["content"]["title"]["text"];
            container.appendChild(h);
        }

        // Mount the author-provided markup (may contain custom elements).
        var mount = document.createElement("div");
        mount.innerHTML = block["content"]["html"] || "";
        container.appendChild(mount);

        // Optional convenience pan/zoom wrapper for raw SVG content. Custom elements
        // generally manage their own pan/zoom, so leave zoomable off for those.
        if (block["content"]["zoomable"] && !mount.querySelector(".zoomable-svg")) {
            mount.classList.add("zoomable-svg");
            mount.style.position = "relative";
            mount.style.overflow = "hidden";
        }

        registerSignal(container, block);
    }

    completion() {
        this.parent.completion(this.blockID, this.completed[0], this.completed[1]);
    }
}

blockLookup["custom_component"] = CustomComponent;
