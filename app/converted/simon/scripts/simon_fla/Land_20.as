package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Land_20 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function Land_20()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 10, this.frame11);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(2);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("simon_land");
                };
            };
        }

        internal function frame4():*
        {
            this.self.endAttack();
        }

        internal function frame11():*
        {
            this.self.endAttack();
        }


    }
}

