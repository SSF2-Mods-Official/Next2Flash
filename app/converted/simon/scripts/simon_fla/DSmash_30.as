package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class DSmash_30 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;
        public var xframe:String;

        public function DSmash_30()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 42, this.frame43, 43, this.frame44, 52, this.frame53, 58, this.frame59, 60, this.frame61, 71, this.frame72);
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
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.xframe = null;
        }

        internal function frame3():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame43():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame44():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
        }

        internal function frame53():*
        {
            this.self.playAttackSound(2);
            this.self.playVoiceSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame59():*
        {
            this.self.refreshAttackID();
        }

        internal function frame61():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame72():*
        {
            this.self.endAttack();
        }


    }
}

