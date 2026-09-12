///<reference path="../gen/BuildConfig.ts"/>

class FeatureFlags{
    private static candyFacadeEnabled: boolean = false;

    public static initialize(urlData: string): void{
        FeatureFlags.candyFacadeEnabled = BuildConfig.cb3CandyFacadeEnabled;

        if(!BuildConfig.isDevelopment()) return;

        var urlValue: string = FeatureFlags.getLastUrlValue(urlData, "cb3CandyFacade");
        var parsedUrlValue: boolean = FeatureFlags.parseBoolean(urlValue);
        if(parsedUrlValue != null){
            FeatureFlags.candyFacadeEnabled = parsedUrlValue;
            return;
        }

        var sessionValue: string = null;
        try{
            sessionValue = sessionStorage.getItem("cb3CandyFacadeEnabled");
        }catch(error){
            sessionValue = null;
        }

        var parsedSessionValue: boolean = FeatureFlags.parseBoolean(sessionValue);
        if(parsedSessionValue != null) FeatureFlags.candyFacadeEnabled = parsedSessionValue;
    }

    public static isCandyFacadeEnabled(): boolean{
        return FeatureFlags.candyFacadeEnabled;
    }

    private static getLastUrlValue(urlData: string, key: string): string{
        if(urlData == null || urlData == "" || urlData.charAt(0) != "?") return null;

        var result: string = null;
        var pairs: string[] = urlData.substr(1).split("&");
        for(var i: number = 0; i < pairs.length; i++){
            var eqIndex: number = pairs[i].indexOf("=");
            if(eqIndex == -1) continue;
            if(pairs[i].substr(0, eqIndex) == key) result = pairs[i].substr(eqIndex + 1);
        }
        return result;
    }

    private static parseBoolean(value: string): boolean{
        if(value == "1") return true;
        if(value == "0") return false;
        return null;
    }
}
