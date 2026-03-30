package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeRoll_74 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function LedgeRoll_74()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 8, this.frame9, 18, this.frame19, 22, this.frame23, 25, this.frame26);
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

        internal function frame4():*
        {
            this.self.playSound("chibi_LedgeClimb");
        }

        internal function frame9():*
        {
            this.self.playSound("run_start");
        }

        internal function frame19():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame23():*
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

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

