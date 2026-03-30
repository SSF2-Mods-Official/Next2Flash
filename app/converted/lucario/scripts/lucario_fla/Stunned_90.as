package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Stunned_90 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Stunned_90()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 15, this.frame16, 19, this.frame20, 34, this.frame35);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame6():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame16():*
        {
            this.self.updateAuraPaws();
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame20():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame35():*
        {
            this.self.updateAuraPaws();
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("lucario_step1");
            };
        }


    }
}

