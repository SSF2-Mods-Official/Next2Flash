package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Dash_18 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function Dash_18()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 7, this.frame8, 8, this.frame9, 14, this.frame15, 18, this.frame19, 19, this.frame20, 22, this.frame23, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.playSound("run_start");
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame8():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame9():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("lucario_step1");
            };
            this.self.updateAuraPaws();
        }

        internal function frame15():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame19():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame20():*
        {
            this.self.playSound("lucario_skid");
            this.self.updateAuraPaws();
        }

        internal function frame23():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame26():*
        {
            this.self.stancePlayFrame("run");
        }


    }
}

