package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class HeavyLand_21 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function HeavyLand_21()
        {
            super();
            addFrameScript(0, this.frame1, 11, this.frame12);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                SSF2API.getCamera().shake(4);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("simon_land");
                };
            };
        }

        internal function frame12():*
        {
            this.self.endAttack();
        }


    }
}

