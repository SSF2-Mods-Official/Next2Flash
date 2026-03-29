package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Taunts_180 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Taunts_180()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 18, this.frame19, 34, this.frame35, 38, this.frame39, 41, this.frame42, 53, this.frame54, 62, this.frame63, 81, this.frame82, 88, this.frame89, 118, this.frame119);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
            };
        }

        internal function frame3():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("falcon_taunt1", true);
            };
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("falcon_footstep");
            };
        }

        internal function frame19():*
        {
            this.self.playSound("cfalcon_taunt_salute");
        }

        internal function frame35():*
        {
            this.self.endAttack();
        }

        internal function frame39():*
        {
            this.self.playSound("falcon_jumpS1");
        }

        internal function frame42():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            };
        }

        internal function frame54():*
        {
            this.self.playSound("cfalcon_taunt_armswing");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            };
        }

        internal function frame63():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("falcon_taunt2", true);
            };
        }

        internal function frame82():*
        {
            this.self.endAttack();
        }

        internal function frame89():*
        {
            this.self.playSound("cfalcon_taunt3", true);
        }

        internal function frame119():*
        {
            this.self.endAttack();
        }


    }
}

