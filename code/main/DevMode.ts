class DevMode {
    public static isEnabled: boolean = false;
    
    public static toggle(): void {
        this.isEnabled = !this.isEnabled;
        console.log("Dev Mode is now: " + this.isEnabled);
    }
}
