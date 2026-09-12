interface CandyRepository extends Disposable{
    getBalance(): number;
    grant(amount: number): boolean;
    spend(amount: number): boolean;
    eatAll(): boolean;
}
