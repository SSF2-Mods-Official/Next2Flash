// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.ItemDashAttack_82

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class ItemDashAttack_82 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function ItemDashAttack_82()
        {
            addFrameScript(0, this.frame1, 5, this.frame6, 7, this.frame8, 23, this.frame24);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame6():*
        {
            this.self.getItem().activateItem();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-7)});
        }

        internal function frame8():*
        {
            this.self.getItem().deactivateItem();
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

