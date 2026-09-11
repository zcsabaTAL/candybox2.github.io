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
        // Guard against an empty "left" (used by QuestLog.addDelimiter()'s blank spacer message):
        // addTwoTags(x, x+0, ...) wraps a zero-width span, and RenderArea's tag-insertion order
        // for two tags sharing one exact (x, y) turns that into a stray "</span><span ...>" --
        // close before open -- which used to be harmless (nothing else was open there to
        // accidentally close) but will eat an *enclosing* wrapper span, like QuestLog.ts's own
        // "quest-log-panel". Skipping the wrap for an empty string changes nothing visually --
        // there was never any text there to style.
        if(this.left != null && this.left.length > 0){
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
