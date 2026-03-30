package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeGetup_73 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function LedgeGetup_73()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 10, this.frame11, 13, this.frame14, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("upSpecUsed", false);
                this.self.setGlobalVariable("nairUsed", false);
                this.self.setIntangibility(true);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("chibi_LedgeClimb");
        }

        internal function frame11():*
        {
            this.self.setXSpeed(6.5, false);
        }

        internal function frame14():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("chibi_DStep");
            };
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}

