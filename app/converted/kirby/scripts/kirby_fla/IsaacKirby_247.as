package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class IsaacKirby_247 extends MovieClip
    {

        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var projMC:*;

        public function IsaacKirby_247()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 9, this.frame10, 10, this.frame11, 29, this.frame30, 30, this.frame31, 38, this.frame39);
        }

        public function checkGrabbed():void
        {
            if (this.self.getGrabbedOpponents()[0])
            {
                this.self.destroyTimer(this.checkGrabbed);
                this.self.attachEffect("isaac_growth", {
                    "x":this.self.getGrabbedOpponents()[0].getX(),
                    "y":(this.self.getY() - 25),
                    "scaleX":((this.self.getGrabbedOpponents()[0].getX() - this.self.getX()) / 155),
                    "absolute":true
                });
                this.self.stancePlayFrame("release");
            };
        }

        public function flipX(_arg_1:Number):*
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.createTimer(1, -1, this.checkGrabbed);
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(-8),
                "y":-15
            });
        }

        internal function frame10():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame11():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }

        internal function frame31():*
        {
            this.self.fireProjectile("isaac_growthProj", this.self.getGrabbedOpponent().getX(), this.self.getGrabbedOpponent().getY(), true);
            this.self.playAttackSound(2);
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }


    }
}

