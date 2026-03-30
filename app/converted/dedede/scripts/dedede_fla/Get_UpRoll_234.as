package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpRoll_234 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;

        public function Get_UpRoll_234()
        {
            super();
            addFrameScript(0, this.frame1, 12, this.frame13, 13, this.frame14, 17, this.frame18);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame14():*
        {
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(5);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_m");
                }
                else
                {
                    this.self.playSound("dedede_land");
                };
            };
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}

