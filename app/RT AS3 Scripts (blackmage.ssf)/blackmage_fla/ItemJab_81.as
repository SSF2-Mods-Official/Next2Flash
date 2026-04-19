// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemJab_81

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemJab_81 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function ItemJab_81()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 12, this.frame13);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame4():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
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
}//package blackmage_fla

