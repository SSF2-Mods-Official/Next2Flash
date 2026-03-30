package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_walking_17 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;

        public function bomberman_walking_17()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 11, this.frame12);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
        }

        internal function frame3():*
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

        internal function frame12():*
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


    }
}

