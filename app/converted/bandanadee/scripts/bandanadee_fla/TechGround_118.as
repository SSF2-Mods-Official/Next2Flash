package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class TechGround_118 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function TechGround_118()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.setGlobalVariable("canStartRise", true);
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("ssf2_snd_vfx_bdee_attack04", true);
                };
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

