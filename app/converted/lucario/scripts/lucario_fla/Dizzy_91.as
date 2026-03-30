package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_91 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Dizzy_91()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 16, this.frame17, 20, this.frame21, 35, this.frame36, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("lucario_dizzy", true);
                };
            };
        }

        internal function frame7():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame17():*
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

        internal function frame21():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame36():*
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

        internal function frame40():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}

