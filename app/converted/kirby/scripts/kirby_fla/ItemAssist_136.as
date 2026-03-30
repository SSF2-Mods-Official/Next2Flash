package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemAssist_136 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function ItemAssist_136()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 16, this.frame17, 26, this.frame27, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame8():*
        {
            this.self.getItem().activateItem();
        }

        internal function frame17():*
        {
            this.self.playSound("kirby_jump1");
        }

        internal function frame27():*
        {
            this.self.attachEffect("effect_kirby_land", {"y":-20});
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

