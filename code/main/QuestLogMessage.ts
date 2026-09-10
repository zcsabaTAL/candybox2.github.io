class QuestLogMessage{
    // Strings
    private left: string = null;
    private right: string = null;
    
    // Should the message be bold ?
    private bold: boolean;
    
    // Constructor
    constructor(left: string, right: string = null, bold: boolean = false){
        // Set the parameters
        this.left = left;
        this.right = right;
        this.bold = bold;
        
        // If the left string is too big
        if(this.left.length > 100 - (this.right != null? this.right.length:0)){
            this.left = this.left.substr(0, 100 - (this.right != null? this.right.length:0) - 7) + " (...)"
        }
    }
    
    // Public methods
    public draw(renderArea: RenderArea, pos: Pos, width: number): void{
        // Give every log line (the delimiter rows drawn by QuestLog itself use their own
        // "quest-log-delimiter" class -- see QuestLog.ts) a shared class so design.css can
        // restyle the whole battle log's typography/spacing without touching this ascii-grid
        // positioning logic at all.
        if(this.left != null){
            renderArea.drawString(this.left, pos.x, pos.y);
            renderArea.addTwoTags(pos.x, pos.x + this.left.length, pos.y, "<span class=\"quest-log-line\">", "</span>");
            if(this.bold) renderArea.addBold(pos.x, pos.x + this.left.length, pos.y);
        }
        if(this.right != null){
            renderArea.drawString(this.right, pos.x + width - this.right.length, pos.y);
            renderArea.addTwoTags(pos.x + width - this.right.length, pos.x + width, pos.y, "<span class=\"quest-log-line quest-log-line-count\">", "</span>");
            if(this.bold) renderArea.addBold(pos.x + width - this.right.length, width, pos.y);
        }
    }
}
