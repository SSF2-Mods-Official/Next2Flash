package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DSmash_103 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;

        public function DSmash_103()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 47, this.frame48, 48, this.frame49, 62, this.frame63);
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

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.gotoAndStop("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame48():*
        {
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
        }

        internal function frame49():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame63():*
        {
            this.self.endAttack();
        }


    }
}

