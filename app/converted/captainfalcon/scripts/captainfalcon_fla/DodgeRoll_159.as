package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class DodgeRoll_159 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var effect:*;

        public function DodgeRoll_159()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 9, this.frame10, 15, this.frame16);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
            };
        }

        internal function frame2():*
        {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.effect.scaleX = -(this.effect.scaleX);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame10():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

