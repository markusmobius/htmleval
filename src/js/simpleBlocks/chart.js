class Chart {
    constructor(root, block, parent, blockID) {
        this.blockID = blockID;
        this.parent = parent;
        this.completed = [0, 0];

        this.div = document.createElement("div");
        root.appendChild(this.div);

        // Title
        if (block.content.title) {
            const h = document.createElement("h" + block.content.title.size);
            h.innerHTML = block.content.title.text;
            this.div.appendChild(h);
        }
    }

    completion() {
        this.parent.completion(this.blockID, this.completed[0], this.completed[1]);
    }
}

class SimpleHistogram extends Chart {
    constructor(root, block, parent, blockID) {
        super(root, block, parent, blockID);

        const width = block.content.width || 400;
        const height = block.content.height || 200;
        const data = block.content.data || [];
        const labels = block.content.labels || [];
        const barColor = block.content.barColor || "#2196F3";
        const maxVal = Math.max(...data, 1);
        
        // Add left margin for y-axis labels
        const leftMargin = 50;
        
        // Adjust SVG height to accommodate x-axis label
        const svgHeight = block.content.xLabel ? height + 30 : height;
        
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("width", width);
        svg.setAttribute("height", svgHeight);
        this.div.appendChild(svg);

        const barWidth = (width - leftMargin) / data.length;
        
        // Draw background grid
        const numTicks = 5;
        for (let t = 0; t <= numTicks; t++) {
            const y = height - 30 - ((height - 40) * t) / numTicks;
            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", leftMargin);
            line.setAttribute("x2", width - 10);
            line.setAttribute("y1", y);
            line.setAttribute("y2", y);
            line.setAttribute("stroke", "#eee");
            line.setAttribute("stroke-width", "1");
            svg.appendChild(line);
            
            const tickVal = Math.round((maxVal * t) / numTicks);
            const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
            label.setAttribute("x", leftMargin - 5);
            label.setAttribute("y", y + 4);
            label.setAttribute("text-anchor", "end");
            label.setAttribute("font-size", "12");
            label.setAttribute("fill", "#555");
            label.textContent = tickVal;
            svg.appendChild(label);
        }

        // Draw bars
        data.forEach((val, i) => {
            // Always show bar, even for zero values
            const barHeight = val === 0 ? 
                2 : // Small height for zero values
                (val / maxVal) * (height - 40);
            
            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", leftMargin + i * barWidth + 5);
            rect.setAttribute("y", height - barHeight - 30);
            rect.setAttribute("width", barWidth - 10);
            rect.setAttribute("height", barHeight);
            rect.setAttribute("fill", val === 0 ? "#dddddd" : barColor);
            svg.appendChild(rect);
            
            // Add tooltip using HTML title attribute which has better browser support
            rect.setAttribute("data-value", val);
            rect.addEventListener("mouseover", (e) => {
                const tooltip = document.createElement("div");
                tooltip.textContent = val;
                tooltip.style.position = "absolute";
                tooltip.style.backgroundColor = "rgba(0,0,0,0.7)";
                tooltip.style.color = "white";
                tooltip.style.padding = "5px";
                tooltip.style.borderRadius = "3px";
                tooltip.style.fontSize = "12px";
                tooltip.style.left = `${e.pageX + 10}px`;
                tooltip.style.top = `${e.pageY - 20}px`;
                tooltip.style.zIndex = "1000";
                tooltip.id = "chart-tooltip";
                document.body.appendChild(tooltip);
            });
            rect.addEventListener("mouseout", () => {
                const tooltip = document.getElementById("chart-tooltip");
                if (tooltip) tooltip.remove();
            });

            // Draw x-axis label
            if (labels[i]) {
                const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                text.setAttribute("x", leftMargin + i * barWidth + barWidth / 2);
                text.setAttribute("y", height - 10);
                text.setAttribute("text-anchor", "middle");
                text.setAttribute("font-size", "8");
                text.textContent = labels[i];
                svg.appendChild(text);
            }
        });
        
        // Y axis label
        if (block.content.yLabel) {
            const yLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
            yLabel.setAttribute("x", 15);
            yLabel.setAttribute("y", height / 2);
            yLabel.setAttribute("text-anchor", "middle");
            yLabel.setAttribute("font-size", "14");
            yLabel.setAttribute("transform", `rotate(-90 15,${height / 2})`);
            yLabel.setAttribute("fill", "#333");
            yLabel.textContent = block.content.yLabel;
            svg.appendChild(yLabel);
        }
        
        // X axis label
        if (block.content.xLabel) {
            const xLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
            xLabel.setAttribute("x", leftMargin + (width - leftMargin) / 2);
            xLabel.setAttribute("y", height + 15);
            xLabel.setAttribute("text-anchor", "middle");
            xLabel.setAttribute("font-size", "14");
            xLabel.setAttribute("fill", "#333");
            xLabel.textContent = block.content.xLabel;
            svg.appendChild(xLabel);
        }
        
        this.completion();
    }
}
// Add to blockLookup
blockLookup["histogram"] = SimpleHistogram;
