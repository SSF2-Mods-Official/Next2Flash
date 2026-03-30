package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_running_18 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_running_18()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 14, this.frame15, 20, this.frame21, 22, this.frame23, 26, this.frame27);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.playSound("bomberman_dash");
            };
        }

        internal function frame7():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame8():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("bomberman_step1");
            };
        }

        internal function frame15():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("bomberman_step2");
            };
        }

        internal function frame21():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame23():*
        {
            this.self.playSound("bomberman_turn");
        }

        internal function frame27():*
        {
            this.self.stancePlayFrame("run");
        }


    }
}

