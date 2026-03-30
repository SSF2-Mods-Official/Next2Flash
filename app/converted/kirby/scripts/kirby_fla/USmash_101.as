package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class USmash_101 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;

        public function USmash_101()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 43, this.frame44, 44, this.frame45, 48, this.frame49, 49, this.frame50, 63, this.frame64);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = null;
        }

        internal function frame4():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame44():*
        {
            this.gotoAndStop("charging");
        }

        internal function frame45():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.playVoiceSound(1);
            this.self.playAttackSound(1);
        }

        internal function frame49():*
        {
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame50():*
        {
            this.self.updateAttackBoxStats(1, {"damage":9});
        }

        internal function frame64():*
        {
            this.self.endAttack();
        }


    }
}

