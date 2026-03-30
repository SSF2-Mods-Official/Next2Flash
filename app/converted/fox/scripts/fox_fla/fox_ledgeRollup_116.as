package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_ledgeRollup_116 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_ledgeRollup_116()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 10, this.frame11, 18, this.frame19, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("fox_jump01");
        }

        internal function frame11():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("fox_landLight");
            };
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

