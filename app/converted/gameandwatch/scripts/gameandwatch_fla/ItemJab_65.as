package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemJab_65 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;

        public function ItemJab_65()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 12, this.frame13);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.playSound("gw_ftilt01");
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
        }

        internal function frame5():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame13():*
        {
            this.self.endAttack();
        }


    }
}

