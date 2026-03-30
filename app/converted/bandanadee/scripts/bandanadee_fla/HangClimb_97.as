package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class HangClimb_97 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function HangClimb_97()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 6, this.frame7, 12, this.frame13, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("bandanadee_jump1");
        }

        internal function frame7():*
        {
            this.self.setXSpeed(6, false);
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("bandanadee_land1");
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

