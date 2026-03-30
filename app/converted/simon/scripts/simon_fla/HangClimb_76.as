package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class HangClimb_76 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function HangClimb_76()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 13, this.frame14, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame4():*
        {
            SSF2API.playSound("simon_dashstart");
        }

        internal function frame7():*
        {
            this.self.setXSpeed(5.5, false);
        }

        internal function frame14():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("simon_land");
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

