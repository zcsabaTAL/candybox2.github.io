class QuestLog{
    // Array of messages contained in the quest log
    private messages: QuestLogMessage[] = [];
    
    // Constructor
    constructor(){

    }
    
    // Public method
    public addDelimiter(): void{
        this.messages.push(new QuestLogMessage("----------------------------------------------------------------------------------------------------"));
        this.messages.push(new QuestLogMessage(""));
    }
    
    public addMessage(message: QuestLogMessage): void{
        // We add the message
        this.messages.push(message);
        
        // We check the log size
        this.checkLogSize();
    }
    
    public draw(renderArea: RenderArea, pos: Pos): void{
        // Wrap the whole block (both delimiter rows and every message row) in one
        // "quest-log-panel" element so design.css can pin the entire thing to a small,
        // scrollable corner box instead of it sitting inline as up to 12 full-width rows --
        // see that class for why (it used to just dominate the screen, especially once the
        // Forest quest's viewport got narrower). This is one element: an opening tag on the
        // first row, a closing tag on the last -- addTag (unlike addTwoTags) isn't limited to
        // a single row, so everything drawn in between, including the delimiter rows' own
        // "quest-log-delimiter" spans and each message's "quest-log-line" span, ends up inside
        // it.
        //
        // The call ORDER below (not the source order you'd naturally reach for) is what makes
        // the nesting actually come out right: RenderArea.getForRendering() inserts every tag
        // for a row via String.addAt(x, ...), processing that row's tags highest-x-first so
        // earlier insertions never shift a not-yet-processed tag's index -- but among tags that
        // share the exact same (x, y), each is inserted at that same numeric index into a string
        // the previous ones have already grown, so whichever tag was added *last* ends up
        // textually first/outermost. Our panel's opening tag shares (pos.x, pos.y) with the top
        // delimiter's opening tag, and our panel's closing tag shares (pos.x+100, pos.y+11) with
        // the bottom delimiter's closing tag -- so to get [panel [delimiter ... delimiter] panel]
        // rather than a mis-nested pair, the panel's open must be added *after* the delimiter's
        // open, and the panel's close must be added *before* the delimiter's close.
        // (pos.x+100 is deliberately avoided here -- it collides with the bottom delimiter's own
        // closing tag at that exact (x, y), and getting the insertion-order tie-break right for two
        // tags sharing one coordinate turned out to be fragile in practice; pos.x+101 lands one
        // column into the same blank padding, closing the panel in the same visual spot with no tie.)
        renderArea.addTag(new RenderTag(pos.x+101, "</span>"), pos.y+11); // panel close, added first (see above)
        
        // We draw the lines
        renderArea.drawHorizontalLine("-", pos.x, pos.x+100, pos.y);
        renderArea.addTwoTags(pos.x, pos.x+100, pos.y, "<span class=\"quest-log-delimiter\">", "</span>");
        renderArea.addTag(new RenderTag(pos.x, "<span class=\"quest-log-panel\">"), pos.y); // panel open, added after the top delimiter's open (see above)
        renderArea.drawHorizontalLine("-", pos.x, pos.x+100, pos.y+11);
        renderArea.addTwoTags(pos.x, pos.x+100, pos.y+11, "<span class=\"quest-log-delimiter\">", "</span>");
        
        // We draw the messages
        for(var i = 0; i < this.messages.length; i++){
            this.messages[i].draw(renderArea, new Pos(pos.x, 1 + pos.y + this.messages.length-1-i), 100);
        }
    }
    
    public getMessageCount(): number{
        return this.messages.length;
    }
    
    public getMessageAt(index: number): QuestLogMessage{
        if(index >= 0 && index < this.messages.length){
            return this.messages[index];
        }
        return null;
    }
    
    public getMessages(): QuestLogMessage[]{
        return this.messages.slice(0);
    }
    
    // Private methods
    private checkLogSize(): void{
        if(this.messages.length > 10){
            this.messages.splice(0, this.messages.length - 10);
        }
    }
}

