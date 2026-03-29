package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class FThrow_61 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:gameandwatchExt;

        public function FThrow_61()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 14, this.frame15, 21, this.frame22, 26, this.frame27, 27, this.frame28, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.playSound("snd_se_GW_Wave02_Mi");
                this.self.forceGrabbedHurtFrame("ball");
            };
        }

        internal function frame8():*
        {
            this.self.playSound("snd_se_GW_Wave03_Mi");
        }

        internal function frame15():*
        {
            this.self.playSound("snd_se_GW_Wave02_Mi");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            };
        }

        internal function frame22():*
        {
            this.self.playSound("snd_se_GW_Wave03_Mi");
        }

        internal function frame27():*
        {
            this.self.playSound("snd_se_GW_Wave02_Mi");
        }

        internal function frame28():*
        {
            SSF2API.getCamera().shake(9);
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

