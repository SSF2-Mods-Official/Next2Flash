package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class SpotDodge_93 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function SpotDodge_93()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 10, this.frame11, 11, this.frame12, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.8,
                "scaleY":0.8
            });
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame12():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("gw_step1");
            };
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

