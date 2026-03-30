package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemHeavyShoot_135 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;

        public function ItemHeavyShoot_135()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(3),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame26():*
        {
            this.self.endAttack();
        }


    }
}

