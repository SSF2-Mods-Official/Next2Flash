package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class Land_24 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;

        public function Land_24()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 13, this.frame14);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(1);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_s");
                }
                else
                {
                    this.self.playSound("chibi_DStep");
                };
            };
        }

        internal function frame5():*
        {
            this.self.endAttack();
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}

