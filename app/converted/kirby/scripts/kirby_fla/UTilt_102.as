package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class UTilt_102 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var playsound:Number;
        public var audio:Number;

        public function UTilt_102()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
            };
        }

        internal function frame3():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-1),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame5():*
        {
            this.self.updateAttackBoxStats(1, {"damage":5});
            this.self.updateAttackBoxStats(2, {"damage":5});
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}

